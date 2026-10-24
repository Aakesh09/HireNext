from rest_framework import serializers

from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resume

        fields = [
            "id",
            "candidate",
            "resume_file",
            "version",
            "ats_score",
            "parsed_text",
            "uploaded_at",
        ]

        read_only_fields = [
            "id",
            "candidate",
            "version",
            "ats_score",
            "parsed_text",
            "uploaded_at",
        ]

    def validate_resume_file(self, file):

        # Allow PDF files only
        if not file.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                "Only PDF files are allowed."
            )

        # Maximum file size: 5 MB
        max_size = 5 * 1024 * 1024

        if file.size > max_size:
            raise serializers.ValidationError(
                "Resume file size must not exceed 5 MB."
            )

        return file