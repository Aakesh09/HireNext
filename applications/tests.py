from datetime import timedelta

from django.test import SimpleTestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import serializers, status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from applications.models import JobApplication
from applications.serializers import RecruiterApplicationSerializer
from candidates.models import CandidateProfile
from companies.models import Company
from jobs.models import Job
from recruiters.models import RecruiterProfile
from resumes.models import Resume


class ApplicationStatusTransitionTests(SimpleTestCase):
    def setUp(self):
        self.application = JobApplication(
            status=JobApplication.Status.APPLIED
        )
        self.serializer = RecruiterApplicationSerializer(
            instance=self.application
        )

    def test_applied_can_transition_to_reviewing(self):
        result = self.serializer.validate_status(
            JobApplication.Status.REVIEWING
        )
        self.assertEqual(result, JobApplication.Status.REVIEWING)

    def test_applied_can_transition_to_rejected(self):
        result = self.serializer.validate_status(
            JobApplication.Status.REJECTED
        )
        self.assertEqual(result, JobApplication.Status.REJECTED)

    def test_same_status_is_allowed(self):
        result = self.serializer.validate_status(
            JobApplication.Status.APPLIED
        )
        self.assertEqual(result, JobApplication.Status.APPLIED)

    def test_applied_cannot_transition_directly_to_selected(self):
        with self.assertRaises(serializers.ValidationError):
            self.serializer.validate_status(
                JobApplication.Status.SELECTED
            )

    def test_selected_is_terminal(self):
        self.application.status = JobApplication.Status.SELECTED

        with self.assertRaises(serializers.ValidationError):
            self.serializer.validate_status(
                JobApplication.Status.REVIEWING
            )

    def test_rejected_is_terminal(self):
        self.application.status = JobApplication.Status.REJECTED

        with self.assertRaises(serializers.ValidationError):
            self.serializer.validate_status(
                JobApplication.Status.REVIEWING
            )

    def test_withdrawn_is_terminal(self):
        self.application.status = JobApplication.Status.WITHDRAWN

        with self.assertRaises(serializers.ValidationError):
            self.serializer.validate_status(
                JobApplication.Status.REVIEWING
            )


class ApplicationSubmissionAPITests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="HireNext Test Technologies",
            slug="hirenext-test-technologies",
            email="contact@hirenext.test",
            industry="Technology",
            company_size=Company.CompanySize.SMALL,
        )

        self.recruiter_user = CustomUser.objects.create_user(
            email="testrecruiter@hirenext.test",
            password="TestPassword123!",
            username="testrecruiter",
            role=CustomUser.Role.RECRUITER,
        )

        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter_user,
            company=self.company,
            designation="Recruiter",
        )

        self.candidate_user = CustomUser.objects.create_user(
            email="candidate1@hirenext.test",
            password="TestPassword123!",
            username="candidate_one",
            first_name="Test",
            last_name="Candidate",
            role=CustomUser.Role.CANDIDATE,
        )

        self.other_candidate_user = CustomUser.objects.create_user(
            email="candidate2@hirenext.test",
            password="TestPassword123!",
            username="candidate_two",
            first_name="Other",
            last_name="Candidate",
            role=CustomUser.Role.CANDIDATE,
        )

        self.candidate = CandidateProfile.objects.create(
            user=self.candidate_user,
            headline="Python Developer",
        )

        self.other_candidate = CandidateProfile.objects.create(
            user=self.other_candidate_user,
            headline="Django Developer",
        )

        self.job = self.create_job()

        # Verify that the test job is associated with the recruiter.
        self.assertEqual(
            self.job.recruiter_id,
            self.recruiter_profile.pk,
        )

        self.client.force_authenticate(user=self.candidate_user)

    def create_job(
        self,
        *,
        title="Python Developer",
        slug="python-developer-test",
        openings=2,
        applications_count=0,
        application_deadline=None,
    ):
        return Job.objects.create(
            company=self.company,
            recruiter=self.recruiter_profile,
            title=title,
            slug=slug,
            description="Build and maintain backend APIs.",
            requirements="Python Django",
            preferred_qualifications="PostgreSQL",
            employment_type=Job.EmploymentType.FULL_TIME,
            work_mode=Job.WorkMode.REMOTE,
            experience_level=Job.ExperienceLevel.ENTRY,
            status=Job.Status.PUBLISHED,
            openings=openings,
            applications_count=applications_count,
            application_deadline=application_deadline,
        )

    def create_resume(self, candidate):
        return Resume.objects.create(
            candidate=candidate,
            resume_file="resumes/test_resume.pdf",
            version=1,
            parsed_text="Python Django PostgreSQL",
        )

    def submit_application(self, job=None, resume=None):
        payload = {
            "job": str((job or self.job).id),
            "cover_letter": "I am interested in this position.",
        }

        if resume is not None:
            payload["resume"] = str(resume.id)

        return self.client.post(
            reverse("apply-job"),
            payload,
            format="json",
        )

    def test_candidate_can_apply_without_resume(self):
        response = self.submit_application()

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        application = JobApplication.objects.get(
            candidate=self.candidate,
            job=self.job,
        )

        self.assertIsNone(application.resume)
        self.assertIsNone(application.resume_version)
        self.assertEqual(
            application.status,
            JobApplication.Status.APPLIED,
        )

        self.job.refresh_from_db()
        self.assertEqual(self.job.applications_count, 1)

    def test_candidate_can_apply_with_own_resume(self):
        resume = self.create_resume(self.candidate)

        response = self.submit_application(resume=resume)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        application = JobApplication.objects.get(
            candidate=self.candidate,
            job=self.job,
        )

        self.assertEqual(application.resume_id, resume.id)
        self.assertEqual(application.resume_version, resume.version)

    def test_candidate_cannot_apply_after_deadline(self):
        expired_job = self.create_job(
            title="Expired Job",
            slug="expired-job-test",
            application_deadline=(
                timezone.localdate() - timedelta(days=1)
            ),
        )

        response = self.submit_application(job=expired_job)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            JobApplication.objects.filter(
                candidate=self.candidate,
                job=expired_job,
            ).exists()
        )

    def test_candidate_cannot_use_another_candidates_resume(self):
        other_resume = self.create_resume(self.other_candidate)

        response = self.submit_application(resume=other_resume)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            JobApplication.objects.filter(
                candidate=self.candidate,
                job=self.job,
            ).exists()
        )

    def test_candidate_cannot_apply_twice_to_same_job(self):
        first_response = self.submit_application()

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.submit_application()

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            JobApplication.objects.filter(
                candidate=self.candidate,
                job=self.job,
            ).count(),
            1,
        )

    def test_candidate_cannot_apply_when_all_openings_are_filled(self):
        full_job = self.create_job(
            title="Fully Booked Job",
            slug="fully-booked-job-test",
            openings=1,
            applications_count=1,
        )

        response = self.submit_application(job=full_job)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            JobApplication.objects.filter(
                candidate=self.candidate,
                job=full_job,
            ).exists()
        )
