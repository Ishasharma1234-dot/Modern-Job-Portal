import random

# Define some possible job types and base details for variety
job_types = ['Full-Time', 'Part-Time', 'Contract', 'Internship']
base_salary = 60000  # Starting base salary
salary_increment = 250  # Increment per job index

for i in range(1, 1001):
    job_title = f"Software Engineer {i}"
    job_type = random.choice(job_types)
    # Generate a salary that starts at base_salary and increments, plus some random variation
    salary_val = base_salary + salary_increment * i + random.randint(-1000, 1000)
    job_salary = f"${salary_val:,}"  # Format salary with comma separators
    job_description = f"Develop awesome software. Position number {i} in our dynamic tech team."
    # Assuming you want all jobs linked to a company with company_id = 1
    company_id = 1

    # Create the INSERT statement
    print(
        f"INSERT INTO job (job_title, job_type, job_salary, job_description, company_id) "
        f"VALUES ('{job_title}', '{job_type}', '{job_salary}', '{job_description}', {company_id});"
    )
