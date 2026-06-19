import jdatetime
from sqlalchemy import Column, Integer, String
from extention import db
from datetime import datetime
import pytz

af_tz = pytz.timezone("Asia/Kabul")


class Manzor_p(db.Model):
    tablename = 'manzor_p'

    id = db.Column(db.Integer, primary_key=True)
    # ... بقیه ستون‌ها
    date = Column(
        String(20),
        default=lambda: jdatetime.datetime.fromgregorian(
            datetime=datetime.now(af_tz)
        ).strftime("%Y-%m-%d")
    )

    m_name = Column(String, nullable=True, index=True)
    mc_name = Column(String, nullable=True, index=True)
    sell_p = Column(Integer, nullable=True, index=True)
    c_p = Column(Integer, nullable=True, index=True)
    d_m = Column(String, nullable=True, index=True)
    quantity = Column(Integer, nullable=True, index=True)
