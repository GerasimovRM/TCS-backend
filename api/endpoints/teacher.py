from typing import Optional
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.site.course import CourseResponse
from models.site.group import GroupResponse
from services.auth_service import get_teacher_or_admin, get_admin
from database import User, Group, UsersGroups, Course, get_session
from database.users_groups import UserGroupRole

router = APIRouter(
    prefix="/teacher",
    tags=["teacher"]
)


@router.post("/create_group", response_model=GroupResponse)
async def create_group(group_name: str,
                       current_user: User = Depends(get_teacher_or_admin),
                       session: AsyncSession = Depends(get_session)) -> GroupResponse:
    group = Group(name=group_name)
    session.add(group)
    await session.commit()
    user_group = UsersGroups(user_group_role=UserGroupRole.OWNER,
                             group=group,
                             user=current_user)
    await user_group.commit()
    return GroupResponse(**group.dict())


@router.post("/create_course", response_model=CourseResponse)
async def create_course(course_name: str,
                        description: Optional[str],
                        current_user: User = Depends(get_admin),
                        session: AsyncSession = Depends(get_session)) -> CourseResponse:
    course = Course(name=course_name)
    if description:
        course.description = description
    session.add(course)
    await session.commit()
    return CourseResponse(**course.dict())

# TODO: add entity to method
"""
@router.post("/add_teacher_or_admin_in_course")  # , response_model=CourseForTeacherOrAdminDto)
async def add_teacher_in_course(course_id: int,
                                user_id: int,
                                current_user: User = Depends(get_teacher_or_admin)):
    course = await Course.objects.get_or_none(id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Course not found")
    user_course = await UsersCourses.objects.get_or_none(user=current_user, course=course)
    if not user_course:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Bad access")
    try:
        is_admin = await get_admin(current_user)
    except HTTPException:
        is_admin = None
    if user_course.user_course_role == UserCourseRole.OWNER or is_admin:
        new_user_course = UsersCourses(user=user_id,
                                       course=course_id,
                                       user_course_role=UserCourseRole.TEACHER)
        await new_user_course.save()
        users = list(map(lambda t: UserDto(**t.user.dict()),
                         await UsersCourses.objects.select_related("user").all(course=course)))
        return CourseForTeacherOrAdminDto(**course.dict(), users=users)
"""