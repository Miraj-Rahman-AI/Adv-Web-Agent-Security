# Research Ethics and Responsible Use

## 1. Research Purpose

AC-DPI-Pilot is intended for authorized research
on Direct Prompt Injection and Web Agent security.

## 2. Experimental Data

The project uses synthetic customer, order,
invoice, billing, and support-ticket records.

All example email addresses use reserved test domains.

No real customer records are required.

## 3. Experimental Isolation

- Use local synthetic environments.
- Avoid production accounts.
- Do not access third-party systems without authorization.
- Do not publish real credentials.
- Do not expose sensitive experimental data.

## 4. Model and Service Security

Service configuration must be stored in environment
variables or appropriate secret-management systems.

Do not commit `.env` files, API keys, passwords,
or private credentials.

## 5. Reporting

Report experimental limitations, unsuccessful trials,
model errors, and baseline authorization failures.

Do not present preliminary synthetic results as
universal Web Agent attack success rates.

## 6. Research Integrity

Preserve raw experimental records.

Document changes to authorization policies.

Do not selectively remove unsuccessful trials.

Distinguish attack attempts from successful
unauthorized execution.

## 7. Scope

The project is a controlled security research
prototype and is not a production attack framework.
