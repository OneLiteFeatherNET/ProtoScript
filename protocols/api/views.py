from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from drf_spectacular.utils import extend_schema
import json
import os
import threading
from django.utils import timezone
from .serializers import ProtocolRequestSerializer, ProtocolJobSerializer, ProtocolResultSerializer
import uuid
from protocols.core.s3_storage import S3Storage
from protocols.core.queue.factory import get_queue_backend

class ProtocolRequestView(APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    @extend_schema(
        summary="Request protocol generation",
        description="Submit a new protocol processing job. Upload a meta.json and a FLAC audio file. Returns a job ID to track progress.",
        request=ProtocolRequestSerializer,
        responses={202: ProtocolJobSerializer},
        tags=["Protocols"]
    )
    def post(self, request, *args, **kwargs):
        serializer = ProtocolRequestSerializer(data=request.data)
        if serializer.is_valid():
            meta_file = serializer.validated_data['meta']
            audio_file = serializer.validated_data['audio']
            template_name = serializer.validated_data.get('template', 'default.md.j2')

            job_id = str(uuid.uuid4())
            storage = S3Storage()

            try:
                # Upload files to S3
                storage.upload_file(f"jobs/{job_id}/meta.json", meta_file)
                storage.upload_file(f"jobs/{job_id}/audio.flac", audio_file)
                
                # Set initial status
                status_data = {
                    'id': job_id,
                    'status': 'pending',
                    'created_at': timezone.now().isoformat(),
                    'template_name': template_name
                }
                storage.update_status(job_id, status_data)
            except Exception as e:
                return Response({'error': f'Failed to upload to S3: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Start background processing
            queue = get_queue_backend()
            queue.enqueue_protocol_job(job_id, template_name=template_name)

            return Response(status_data, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProtocolResultView(APIView):
    @extend_schema(
        summary="Get protocol job result",
        description="Retrieve the status or the final markdown result of a previously submitted protocol job.",
        responses={200: ProtocolResultSerializer},
        tags=["Protocols"]
    )
    def get(self, request, job_id, *args, **kwargs):
        storage = S3Storage()
        status_data = storage.get_status(job_id)
        
        if not status_data:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

        if status_data.get('status') == 'completed':
            result_markdown = storage.get_result(job_id)
            status_data['result_markdown'] = result_markdown
            return Response(status_data)
        
        return Response(status_data)
