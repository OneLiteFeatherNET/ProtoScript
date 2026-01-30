from rest_framework import serializers

class ProtocolRequestSerializer(serializers.Serializer):
    meta = serializers.FileField(
        required=True, 
        help_text="The meta.json file containing user information and events."
    )
    audio = serializers.FileField(
        required=True, 
        help_text="The audio FLAC file to be transcribed."
    )
    template = serializers.CharField(
        required=False, 
        default='default.md.j2', 
        help_text="Name of the Jinja2 template to use for rendering (e.g., 'default.md.j2' or 'discord.md.j2')."
    )

class ProtocolJobSerializer(serializers.Serializer):
    id = serializers.UUIDField(help_text="Unique identifier for the protocol job.")
    status = serializers.ChoiceField(
        choices=['pending', 'processing', 'completed', 'failed'],
        help_text="Current status of the job."
    )
    created_at = serializers.DateTimeField(required=False, help_text="Timestamp when the job was created.")
    completed_at = serializers.DateTimeField(required=False, help_text="Timestamp when the job was finished.")
    error_message = serializers.CharField(required=False, help_text="Error message if the job failed.")

class ProtocolResultSerializer(serializers.Serializer):
    id = serializers.UUIDField(help_text="Unique identifier for the protocol job.")
    status = serializers.ChoiceField(
        choices=['pending', 'processing', 'completed', 'failed'],
        help_text="Current status of the job."
    )
    result_markdown = serializers.CharField(required=False, help_text="The generated markdown protocol (only available if status is 'completed').")
    error_message = serializers.CharField(required=False, help_text="Error message if the job failed.")
    completed_at = serializers.DateTimeField(required=False, help_text="Timestamp when the job was finished.")
