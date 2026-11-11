import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from domain.entities.template import Template
from domain.value_objects.channel import Channel
from infrastructure.persistence.sql_template_repository import SqlTemplateRepository


def make_template(**overrides) -> Template:
    params = dict(
        name=f"template-{uuid.uuid4()}",
        channel=Channel.EMAIL,
        body_template="Olá, {{ name }}!",
        subject_template="Bem-vindo, {{ name }}",
    )
    params.update(overrides)
    return Template(**params)


async def save_and_commit(session_factory, template: Template) -> None:
    async with session_factory() as session:
        await SqlTemplateRepository(session).save(template)
        await session.commit()


async def get_by_id(session_factory, template_id):
    async with session_factory() as session:
        return await SqlTemplateRepository(session).get_by_id(template_id)


async def test_save_and_get_by_id_roundtrip(session_factory, created_template_ids):
    original = make_template()
    created_template_ids.append(original.id)

    await save_and_commit(session_factory, original)
    loaded = await get_by_id(session_factory, original.id)

    assert loaded is not None
    assert loaded.id == original.id
    assert loaded.name == original.name
    assert loaded.channel == Channel.EMAIL
    assert loaded.subject_template == original.subject_template
    assert loaded.body_template == original.body_template
    assert loaded.created_at == original.created_at
    assert loaded.updated_at == original.updated_at


async def test_template_without_subject(session_factory, created_template_ids):
    original = make_template(channel=Channel.SMS, subject_template=None)
    created_template_ids.append(original.id)

    await save_and_commit(session_factory, original)
    loaded = await get_by_id(session_factory, original.id)

    assert loaded.channel == Channel.SMS
    assert loaded.subject_template is None


async def test_get_by_id_returns_none_when_not_found(session_factory):
    assert await get_by_id(session_factory, uuid.uuid4()) is None


async def test_get_by_name(session_factory, created_template_ids):
    original = make_template()
    created_template_ids.append(original.id)
    await save_and_commit(session_factory, original)

    async with session_factory() as session:
        found = await SqlTemplateRepository(session).get_by_name(original.name)
        missing = await SqlTemplateRepository(session).get_by_name("nao-existe")

    assert found is not None
    assert found.id == original.id
    assert missing is None


async def test_save_updates_existing_template(session_factory, created_template_ids):
    original = make_template()
    created_template_ids.append(original.id)
    await save_and_commit(session_factory, original)

    original.update(name=original.name, body_template="Novo corpo", subject_template="Novo assunto")
    await save_and_commit(session_factory, original)

    loaded = await get_by_id(session_factory, original.id)
    assert loaded.body_template == "Novo corpo"
    assert loaded.subject_template == "Novo assunto"
    assert loaded.updated_at == original.updated_at


async def test_list_all_returns_templates_ordered_by_name(session_factory, created_template_ids):
    prefix = f"list-{uuid.uuid4()}"
    templates = [make_template(name=f"{prefix}-{letter}") for letter in ("c", "a", "b")]
    for template in templates:
        created_template_ids.append(template.id)
        await save_and_commit(session_factory, template)

    async with session_factory() as session:
        all_templates = await SqlTemplateRepository(session).list_all()

    names = [t.name for t in all_templates if t.name.startswith(prefix)]
    assert names == [f"{prefix}-a", f"{prefix}-b", f"{prefix}-c"]
    assert all(isinstance(t, Template) for t in all_templates)


async def test_delete_removes_template(session_factory, created_template_ids):
    original = make_template()
    created_template_ids.append(original.id)
    await save_and_commit(session_factory, original)

    async with session_factory() as session:
        await SqlTemplateRepository(session).delete(original.id)
        await session.commit()

    assert await get_by_id(session_factory, original.id) is None


async def test_delete_nonexistent_template_does_not_raise(session_factory):
    async with session_factory() as session:
        await SqlTemplateRepository(session).delete(uuid.uuid4())
        await session.commit()


async def test_duplicate_name_raises_integrity_error(session_factory, created_template_ids):
    first = make_template()
    created_template_ids.append(first.id)
    await save_and_commit(session_factory, first)

    duplicate = make_template(name=first.name)
    created_template_ids.append(duplicate.id)

    with pytest.raises(IntegrityError):
        await save_and_commit(session_factory, duplicate)
