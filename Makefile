PROJECT = sublime_ansible_vault
PYTHON_VERSION = 3.8.1
PYTHON_DOCKER_IMAGE = python:$(PYTHON_VERSION)-buster
ANSIBLE_VERSIONS = 4.7.0 4.0.0 3.3.0 2.10.5 2.5.10

DOCKER_CMD = docker run \
		--rm \
		-v $(shell pwd):/$(PROJECT) \
		-w /$(PROJECT) \
		$(PYTHON_DOCKER_IMAGE) bash -c

COVERAGE_OPTS= \
	--cov-report=term-missing \
	--cov-report=html:coverage

define DOCKER
	$(DOCKER_CMD) "pip install -r tests/requirements.txt && $(1)"

endef

.PHONY: test-suite
test-suite: test flake pydocstyle     ## (Default) Run all tests.

.PHONY: pydocstyle
pydocstyle:                           ## Run pydocstyle.
	$(call DOCKER,pydocstyle)

.PHONY: flake
flake:                                ## Run flake8.
	$(call DOCKER,flake8)

.PHONY: coverage
coverage:                                ## Generate coverage report.
	$(call DOCKER,pytest $(COVERAGE_OPTS))

.PHONY: test
test:                                 ## Run pytest against multiple Ansible versions.
	$(foreach v,$(ANSIBLE_VERSIONS),make test-$(v))

.PHONY: test-%
test-%:                               ## Run pytest against a specific Ansible version.
	$(call DOCKER,pip install ansible==$* && pytest)

.PHONY: help
help:                                 ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
