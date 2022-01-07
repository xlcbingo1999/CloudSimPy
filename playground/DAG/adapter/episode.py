from playground.auxiliary.episode import Episode
from .broker import JobBroker

Episode.broker_cls = JobBroker
