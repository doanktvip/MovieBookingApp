import pytest
from flask import Flask

from movieapp import db
from movieapp.models import Cinema


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.init_app(app)

    return app

@pytest.fixture
def test_app():
    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()

@pytest.fixture
def sample_cinemas(test_session):
    c1=Cinema(name="CGV Tân Phú",address="30 Tân Thắng, Sơn Kỳ, Quận Tân Phú, TP.HCM",province_id=1,map_url="hi")
    c2 = Cinema(name="CGV Crescent Mall", address="12 Tôn Dật Tiên, Phú Mỹ Hưng, TP.HCM", province_id=1, map_url="hi")
    c3 = Cinema(name="CGV Yên Lãng", address="120 Yên Lãng, Quận Hà Tây, Hà Nội", province_id=2, map_url="hi")
    test_session.add_all([c1,c2,c3])
    test_session.commit()

    yield c1,c2,c3
