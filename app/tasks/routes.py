from fastapi import APIRouter, Path, Depends, HTTPException, Query
from fastapi.responses import Response
from tasks.schemas import TaskResponseSchema, TaskCreateSchema, TaskUpdateSchema
from tasks.models import TaskModel
from sqlalchemy.orm import Session
from core.database import get_db
from typing import List


router = APIRouter(tags=["tasks"])


@router.get("/tasks", response_model=List[TaskResponseSchema])
async def retrieve_tasks_list(completed: bool = Query(None, description="Filter by completed status"),
                              limit: int =  Query(10, gt=0, le=50, description="Limiting the number of item to retrieve"),
                              offset: int =  Query(0, ge=0, description="how many items to retrieve"),
                              db: Session = Depends(get_db)):

    query = db.query(TaskModel)
    if completed:
        query = query.filter_by(is_completed=completed)
    return query.limit(limit).offset(offset).all()


@router.get("/tasks/{task_id}", response_model=TaskResponseSchema)
async def retrieve_tasks_detail(task_id : int = Path(..., gt=0), db: Session = Depends(get_db)):
    task_obj = db.query(TaskModel).filter_by(id = task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_obj


@router.post("/tasks", response_model=TaskResponseSchema)
async def create_task(request: TaskCreateSchema, db: Session = Depends(get_db)):
    task_obj = TaskModel(**request.model_dump())
    db.add(task_obj)
    db.commit()
    db.refresh(task_obj)
    return task_obj


@router.put("/tasks/{task_id}", response_model=TaskResponseSchema)
async def update_task(request: TaskUpdateSchema, task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task_obj = db.query(TaskModel).filter_by(id = task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(task_obj, field, value)

    db.commit()
    db.refresh(task_obj)
    return task_obj


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task_obj = db.query(TaskModel).filter_by(id = task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task_obj)
    db.commit()
    return Response(status_code=204)