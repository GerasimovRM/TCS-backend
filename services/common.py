from typing import Optional

from pydantic import BaseModel, create_model


def exclude_fields(to_exclude_fields: list[str]):
    def class_decorator(base_class: BaseModel):
        fields = base_class.__fields__
        bad_fields = set(to_exclude_fields) - set(fields)
        if bad_fields:
            raise ValueError(f"Bad key for field{'' if len(bad_fields) == 1 else 's'}: {', '.join(bad_fields)}")
        validators = {"__validators__": base_class.__validators__}
        new_fields = {key: (item.type_, ... if item.required else None) for key, item in
                      fields.items() if key not in to_exclude_fields}
        return create_model(base_class.__name__,
                            **new_fields, __validators__=validators)

    return class_decorator


def exclude_field(to_exclude_field):
    return exclude_fields([to_exclude_field])


def make_fields_required(to_required_fields: list[str]):
    def class_decorator(base_class: BaseModel):
        fields = base_class.__fields__
        bad_fields = set(to_required_fields) - set(fields)
        if bad_fields:
            raise ValueError(f"Bad key for field{'' if len(bad_fields) == 1 else 's'}: {', '.join(bad_fields)}")
        validators = {"__validators__": base_class.__validators__}
        new_fields = {key: (item.type_, ... if item.required or key in to_required_fields else None) for key, item in
                      fields.items()}
        return create_model(base_class.__name__,
                            **new_fields, __validators__=validators)

    return class_decorator


def make_field_required(to_required_field: str):
    return make_fields_required([to_required_field])


def make_fields_non_required(to_non_required_fields: list[str]):
    def class_decorator(base_class: BaseModel):
        fields = base_class.__fields__
        bad_fields = set(to_non_required_fields) - set(fields)
        if bad_fields:
            raise ValueError(f"Bad key for field{'' if len(bad_fields) == 1 else 's'}: {', '.join(bad_fields)}")
        validators = {"__validators__": base_class.__validators__}
        new_fields = {key: (item.type_, ... if item.required else None) for key, item in
                      fields.items()}
        for key, item in new_fields.items():
            if key in new_fields:
                new_fields[key] = (item[0], None)
        return create_model(base_class.__name__,
                            **new_fields, __validators__=validators)

    return class_decorator


def make_field_non_required(to_non_required_field: str):
    return make_fields_non_required([to_non_required_field])


if __name__ == "__main__":
    class TestClass(BaseModel):
        id: int
        score: float
        test_field: Optional[str]


    @exclude_field("id")
    class TestClassWithoutId(TestClass):
        ...

    @make_fields_required(["test_field"])
    class TestClassWithRequiredTestField(TestClassWithoutId):
        ...

    print(TestClassWithRequiredTestField(score=3, id=2, test_field=4))
    print(TestClassWithoutId(score=3))
    print(TestClass(id=3, score=4))


    @make_fields_non_required(["score2"])
    class TestClassWithNonRequiredFields(TestClassWithoutId):
        ...

    print(TestClassWithNonRequiredFields(id=3, score=4, test_field=5))

