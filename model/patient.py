import jdatetime
from sqlalchemy import Column, Integer, String
from extention import db
from datetime import datetime
import pytz

af_tz = pytz.timezone("Asia/Kabul")


class Patient(db.Model):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, index=True)
    fathername = Column(String, nullable=False, index=True)
    gender = Column(String, nullable=True, index=True)
    address = Column(String, nullable=True, index=True)
    fee = Column(Integer, nullable=True, index=True, default=0)
    p_fee = Column(Integer, nullable=True, index=True, default=0)
    m_f = Column(Integer, nullable=True, index=True)
    profit = Column(Integer, nullable=True, index=True, default=0)
    date = Column(
        String(20),
        default=lambda: jdatetime.datetime.fromgregorian(
            datetime=datetime.now(af_tz)
        ).strftime("%Y-%m-%d")
    )
    number = Column(String(10), nullable=True, index=True)
    p_number = Column(Integer, nullable=True, index=True)
    u_s = Column(Integer, nullable=True, index=True)
    neb = Column(String, nullable=True, index=True)
    iv_c = Column(Integer, nullable=True, index=True)
    im = Column(String, nullable=True, index=True)
    db_type = Column(String, nullable=True, index=True)
    loan = Column(Integer, nullable=True, index=True, default=0)
    ePname =Column(String, nullable=True, index=True)
    eFname = Column(String, nullable=True, index=True)