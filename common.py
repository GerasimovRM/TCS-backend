from pydantic import BaseModel, create_model


def exclude_fields(to_exclude_fields: list):
    def class_decorator(base_class: BaseModel):
        fields = base_class.__fields__
        validators = {"__validators__": base_class.__validators__}
        new_fields = {key: (item.type_, ... if item.required else None) for key, item in
                      fields.items() if key not in to_exclude_fields}
        return create_model(base_class.__name__,
                            **new_fields, __validators__=validators)

    return class_decorator


def exclude_field(to_exclude_field):
    return exclude_fields([to_exclude_field])


if __name__ == "__main__":
    @exclude_fields(["id"])
    class TestClass(BaseModel):
        id: int
        score: float


    print(TestClass(score=4))
