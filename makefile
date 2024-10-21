template_name ?= default

generate:
	python3 code/project_template_creator.py --template_name=$(template_name)