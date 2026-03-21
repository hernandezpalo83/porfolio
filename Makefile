.PHONY: test coverage lint migrate run

test:
	python manage.py test --verbosity=2

coverage:
	coverage run manage.py test
	coverage report
	coverage html

lint:
	ruff check app/ --fix

migrate:
	python manage.py makemigrations
	python manage.py migrate

run:
	python manage.py runserver
