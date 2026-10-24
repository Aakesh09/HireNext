
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from companies.models import Company
from recruiters.models import RecruiterProfile
from jobs.models import Job


class JobAPITests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="HireNext Technologies",
            slug="hirenext-technologies",
            email="contact@hirenext.test",
            industry="Technology",
            company_size=Company.CompanySize.SMALL,
        )

        self.other_company = Company.objects.create(
            name="Other Technologies",
            slug="other-technologies",
            email="contact@other.test",
            industry="Technology",
            company_size=Company.CompanySize.SMALL,
        )

        self.recruiter_user = CustomUser.objects.create_user(
            email="recruiter@hirenext.test",
            password="TestPassword123!",
            username="hirenext_recruiter",
            first_name="HireNext",
            last_name="Recruiter",
            role="RECRUITER",
        )

        self.other_recruiter_user = CustomUser.objects.create_user(
            email="recruiter@other.test",
            password="TestPassword123!",
            username="other_recruiter",
            first_name="Other",
            last_name="Recruiter",
            role="RECRUITER",
        )

        self.candidate_user = CustomUser.objects.create_user(
            email="candidate@hirenext.test",
            password="TestPassword123!",
            username="test_candidate",
            first_name="Test",
            last_name="Candidate",
            role="CANDIDATE",
        )

        self.recruiter = RecruiterProfile.objects.create(
            user=self.recruiter_user,
            company=self.company,
            designation="HR Manager",
        )

        self.other_recruiter = RecruiterProfile.objects.create(
            user=self.other_recruiter_user,
            company=self.other_company,
            designation="HR Manager",
        )

        self.published_job = self.create_job(
            title="Python Developer",
            slug="python-developer",
            recruiter=self.recruiter,
            company=self.company,
            job_status=Job.Status.PUBLISHED,
        )

        self.draft_job = self.create_job(
            title="Django Developer",
            slug="django-developer",
            recruiter=self.recruiter,
            company=self.company,
            job_status=Job.Status.DRAFT,
        )

        self.other_recruiter_job = self.create_job(
            title="Java Developer",
            slug="java-developer",
            recruiter=self.other_recruiter,
            company=self.other_company,
            job_status=Job.Status.PUBLISHED,
        )

    def get_response_items(self, response):
        """Support both paginated and non-paginated API responses."""
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]

        return response.data

    def create_job(
        self,
        title,
        slug,
        recruiter,
        company,
        job_status,
    ):
        job = Job.objects.create(
            company=company,
            recruiter=recruiter,
            title=title,
            slug=slug,
            description=f"Job description for {title}",
            employment_type=Job.EmploymentType.FULL_TIME,
            work_mode=Job.WorkMode.REMOTE,
            experience_level=Job.ExperienceLevel.ENTRY,
            status=job_status,
        )

        if job_status == Job.Status.PUBLISHED:
            job.published_at = timezone.now()
            job.save(update_fields=["published_at"])

        return job

    def test_public_list_shows_only_published_jobs(self):
        response = self.client.get(reverse("job-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        items = self.get_response_items(response)
        returned_ids = {item["id"] for item in items}

        self.assertIn(str(self.published_job.id), returned_ids)
        self.assertNotIn(str(self.draft_job.id), returned_ids)

    def test_public_job_search_filters_by_title(self):
        response = self.client.get(
            reverse("job-list"),
            {"search": "Python"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        items = self.get_response_items(response)
        returned_titles = {item["title"] for item in items}

        self.assertIn("Python Developer", returned_titles)
        self.assertNotIn("Django Developer", returned_titles)

    def test_public_user_cannot_retrieve_draft_job(self):
        response = self.client.get(
            reverse(
                "job-detail",
                kwargs={"id": self.draft_job.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_recruiter_list_contains_only_own_jobs(self):
        self.client.force_authenticate(
            user=self.recruiter_user
        )

        response = self.client.get(
            reverse("recruiter-job-list")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        items = self.get_response_items(response)
        returned_ids = {item["id"] for item in items}

        self.assertIn(str(self.published_job.id), returned_ids)
        self.assertIn(str(self.draft_job.id), returned_ids)
        self.assertNotIn(
            str(self.other_recruiter_job.id),
            returned_ids,
        )

    def test_recruiter_cannot_update_another_recruiters_job(self):
        self.client.force_authenticate(
            user=self.recruiter_user
        )

        response = self.client.patch(
            reverse(
                "recruiter-job-update",
                kwargs={"id": self.other_recruiter_job.id},
            ),
            {"title": "Unauthorized title change"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.other_recruiter_job.refresh_from_db()
        self.assertEqual(
            self.other_recruiter_job.title,
            "Java Developer",
        )

    def test_recruiter_can_create_a_draft_job(self):
        self.client.force_authenticate(
            user=self.recruiter_user
        )

        payload = {
            "company": str(self.company.id),
            "title": "Backend Developer",
            "slug": "backend-developer",
            "description": "Build and maintain backend APIs.",
            "employment_type": "FULL_TIME",
            "work_mode": "REMOTE",
            "experience_level": "ENTRY",
            "minimum_experience": 0,
            "maximum_experience": 2,
            "openings": 2,
        }

        response = self.client.post(
            reverse("recruiter-job-create"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_job = Job.objects.get(
            slug="backend-developer"
        )

        self.assertEqual(
            created_job.recruiter_id,
            self.recruiter.id,
        )
        self.assertEqual(
            created_job.status,
            Job.Status.DRAFT,
        )

    def test_recruiter_cannot_create_job_for_another_company(self):
        self.client.force_authenticate(
            user=self.recruiter_user
        )

        payload = {
            "company": str(self.other_company.id),
            "title": "Unauthorized Job",
            "slug": "unauthorized-job",
            "description": "This job should not be created.",
            "employment_type": "FULL_TIME",
            "work_mode": "REMOTE",
            "experience_level": "ENTRY",
        }

        response = self.client.post(
            reverse("recruiter-job-create"),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(
            Job.objects.filter(slug="unauthorized-job").exists()
        )

    def test_recruiter_can_publish_own_draft_job(self):
        self.client.force_authenticate(
            user=self.recruiter_user
        )

        response = self.client.patch(
            reverse(
                "recruiter-job-publish",
                kwargs={"id": self.draft_job.id},
            ),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.draft_job.refresh_from_db()
        self.assertEqual(
            self.draft_job.status,
            Job.Status.PUBLISHED,
        )
        self.assertIsNotNone(self.draft_job.published_at)

    def test_recruiter_cannot_publish_another_recruiters_job(self):
        self.client.force_authenticate(
            user=self.recruiter_user
        )

        response = self.client.patch(
            reverse(
                "recruiter-job-publish",
                kwargs={"id": self.other_recruiter_job.id},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_candidate_cannot_access_recruiter_job_list(self):
        self.client.force_authenticate(
            user=self.candidate_user
        )

        response = self.client.get(
            reverse("recruiter-job-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
