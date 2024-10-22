import datetime as dt
from decimal import Decimal
import uuid

import arrow
import pytest

from .apps.alpha import AlphaApp, Bag, Blog, Category, Project, Task, db, delete_all


@pytest.fixture(scope='module')
def app():
    app = AlphaApp.create(testing=True, init_app=False)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.init_app(None)
    return app


@pytest.fixture
def db_clear(app: AlphaApp):
    with app.app_context():
        delete_all()
        yield
        db.session.remove()


@pytest.mark.usefixtures('db_clear')
class TestFakerMixin:
    def test_basics(self):
        bag = Bag.fake()
        assert bag.name and isinstance(bag.name, str)
        assert bag.order and isinstance(bag.order, int)
        assert bag.date and isinstance(bag.date, dt.date)
        assert bag.datetime and isinstance(bag.datetime, dt.datetime)
        assert bag.amount and isinstance(bag.amount, Decimal)
        assert bag.weight and isinstance(bag.weight, float)
        assert bag.active is not None and isinstance(bag.active, bool)
        assert bag.arrow and isinstance(bag.arrow, arrow.Arrow)
        assert '@' in bag.email and isinstance(bag.email, str)
        assert bag.temp.value in ('hot', 'cold')
        assert bag.ident and isinstance(bag.ident, uuid.UUID)

        assert bag.skip_a is None
        assert bag.skip_b == '10'
        assert bag.skip_c == '11'

        bag2 = Bag.fake()
        assert bag2.id == bag.id + 1

    def test_relationship(self):
        task = Task.fake()
        assert task.project.name

        task = Task.fake(project__name='foo')
        assert task.project.name == 'foo'

        proj = Project.fake()
        task = Task.fake(project=proj)
        assert task.project is proj

        task = Task.fake(project_id=proj.id)
        assert task.project is proj

    def test_relationship_conflicting_values(self):
        proj = Project.fake()
        with pytest.raises(ValueError) as exc_info:
            Task.fake(project=proj, project__name='foo')
        assert (
            str(exc_info.value)
            == "Value for 'project' given but kwargs given for it also: {'name': 'foo'}"
        )

    def test_relationship_id_and_obj_given(self):
        proj = Project.fake()
        with pytest.raises(ValueError) as exc_info:
            Task.fake(project=proj, project_id=proj.id)
        assert (
            str(exc_info.value)
            == "Value for 'project' given but the relationship's FK columns were also given: ['project_id']"  # noqa: E501
        )

    def test_relationship_id_and_rel_kwargs_given(self):
        proj = Project.fake()
        with pytest.raises(ValueError) as exc_info:
            Task.fake(project_id=proj.id, project__name='foo')
        assert (
            str(exc_info.value)
            == "Relationship kwargs given ({'name': 'foo'}) but the relationship's FK columns were also given: ['project_id']"  # noqa: E501
        )

    def test_relationship_optional(self):
        blog = Blog.fake()
        assert blog.category is None

        blog = Blog.fake(category=Category.FAKE_IT)
        assert blog.category

    def test_provided(self):
        bag = Bag.fake(name='foo')
        assert bag.name == 'foo'

        bag = Bag.fake(name=Bag.FAKE_IT)
        assert bag.name


@pytest.mark.usefixtures('db_clear')
class TestDecorators:
    def test_session_execute(self):
        task = Task.fake(due=dt.date(2024, 1, 1))
        result = Task.select_due()
        tasks = result.all()
        assert len(tasks) == 1
        assert tasks[0] == (task,)

    def test_session_scalars(self):
        task = Task.fake(due=dt.date(2024, 1, 1))
        result = Task.select_due2()
        tasks = result.all()
        assert len(tasks) == 1
        assert tasks[0] == task
