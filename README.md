# LLM-Driven Property Rewriting Project
This project is a Django-based CLI application designed to rewrite property information (titles and descriptions) using a Large Language Model (LLM). It integrates with the Ollama API to generate enhanced property summaries, reviews, and ratings. The project leverages Docker for containerized deployment and PostgreSQL for database management. It also incorporates data from a Scrapy project that scrapes hotel property information.
Features

## LLM Integration:

- Rewrite property titles and descriptions using Gemini API key.

- Generate property summaries, customer reviews, and ratings.

- Django CLI Application:

    - Perform operations through a command-line interface.

    - Manage rewritten property data effectively.

- Database Management:

     - PostgreSQL database to store original and rewritten property data.

     - Supports Dockerized database setup for seamless deployment.

Scrapy Integration:

- Pull property data from a Scrapy project.

- Synchronize data between Scrapy and Django.

Containerized Deployment:

- Dockerized setup for easy deployment and management.

- Includes PostgreSQL and pgAdmin containers.

## Run this project
first go to my scrapy project which project i scrap hotel information. Follow the `Readme.md` file for this project. Because before run LLM project this project must need to be run.
This is the github website link of this project.
```
https://github.com/siam29/Scarpy-master
```
After run this project then we need to run our LLM project.  
Clone this project
```
git clone https://github.com/siam29/Assignment-LLM.git
```
create environment
```
python3 -m venv django_env
```
active this environment
```
source django_env/bin/activate
```
```
cd Assignment-LLM/
```
```
docker-compose up --build
```
- Rewrite hotel titles
```
docker-compose exec django_app python manage.py rewrite_titles --batch-size 2
```
- Generate hotel descriptions
```
docker-compose exec django_app python manage.py generate_descriptions --batch-size 2
```
### Future Enhancements

- Add a user-friendly frontend for managing property data.

- Extend LLM capabilities to generate additional content (e.g., FAQs).

- Implement caching for LLM responses to improve performance.

- Integrate with third-party property management systems.