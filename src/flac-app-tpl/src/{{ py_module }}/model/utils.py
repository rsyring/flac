from flac.contrib.sqlalchemy import DefaultColsMixin, FakerMixin, MethodsMixin


class EntityMixin(FakerMixin, MethodsMixin, DefaultColsMixin):
    pass
