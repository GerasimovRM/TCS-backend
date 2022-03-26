from typing import Optional
from fastapi import APIRouter, status, HTTPException, Depends

from services.auth_service import get_teacher_or_admin, get_admin
from database import User, Group, UsersGroups, Course
from database.users_groups import UserGroupRole
from models import GroupDto, CourseDto, CourseForTeacherOrAdminDto, UserDto


router = APIRouter(
    prefix="/teacher",
    tags=["teacher"]
)


@router.post("/create_group", response_model=GroupDto)
async def create_group(group_name: str,
                       current_user: User = Depends(get_teacher_or_admin)):
    group = Group(name=group_name)
    await group.save()
    user_group = UsersGroups(user_group_role=UserGroupRole.OWNER,
                             group=group,
                             user=current_user)
    await user_group.save()
    return GroupDto(**group.dict())


@router.post("/create_course", response_model=CourseDto)
async def create_course(course_name: str,
                        description: Optional[str],
                        current_user: User = Depends(get_teacher_or_admin)):
    course = Course(name=course_name)
    if description:
        course.description = description
    await course.save()
    user_course = UsersCourses(user_course_role=UserCourseRole.OWNER,
                               course=course,
                               user=current_user)
    await user_course.save()
    return CourseDto(**course.dict())


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
