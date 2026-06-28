import jdatetime
from sqlalchemy import Column, Integer, String
from extention import db
from datetime import datetime
import pytz

af_tz = pytz.timezone("Asia/Kabul")


class E_Money(db.Model):
    __tablename__ = "e_moneys"

    id = Column(Integer, primary_key=True, index=True)
    e_m = Column(Integer, nullable=False, index=True)
    e_r = Column(String, nullable=False, index=True)

    date = Column(
        String(20),
        default=lambda: jdatetime.datetime.fromgregorian(
            datetime=datetime.now(af_tz)
        ).strftime("%Y-%m-%d")
    )
