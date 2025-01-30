from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.base import JobLookupError


#not used for now
class CustomSQLAlchemyJobStore(SQLAlchemyJobStore):
    def add_job(self, job):
        """
        Custom job insertion logic.
        """
        print(f"Adding job: {job.id}")
        # Call the original method to insert the job
        super().add_job(job)
    
    def remove_job(self, job_id):
        """
        Custom job removal logic.
        """
        print(f"Removing job: {job_id}")
        # Call the original method to remove the job
        super().remove_job(job_id)