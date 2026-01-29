from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.deps import get_db, admin_only
from models.tool import Tool
from schemas.tool import ToolCreate, ToolUpdate

router = APIRouter(prefix="/tools", tags=["Tools"])

from sqlalchemy import or_

@router.get("")
async def list_tools(
        db: AsyncSession = Depends(get_db),
        page: int = 1,
        page_size: int = 9,
        search: str = ""
):
    skip = (page - 1) * page_size
    query = select(Tool)
    if search:
        query = query.where(
            or_(
                Tool.name.ilike(f"%{search}%"),
                Tool.description.ilike(f"%{search}%")
            )
        )

    count_stmt = select(func.count()).select_from(query.subquery())
    total_count = (await db.execute(count_stmt)).scalar()

    result = await db.execute(query.offset(skip).limit(page_size))
    tools = result.scalars().all()

    return {
        "items": tools,
        "total_pages": (total_count + page_size - 1) // page_size,
        "current_page": page
    }

@router.get("/{tool_id}")
async def get_tool(tool_id: int, db: AsyncSession = Depends(get_db)):
    tool = await db.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@router.post("", dependencies=[Depends(admin_only)])
async def create_tool(
    payload: ToolCreate,
    db: AsyncSession = Depends(get_db),
):
    tool = Tool(**payload.model_dump())
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


@router.put("/{tool_id}", dependencies=[Depends(admin_only)])
async def update_tool(
    tool_id: int,
    payload: ToolUpdate,
    db: AsyncSession = Depends(get_db),
):
    tool = await db.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tool, field, value)

    await db.commit()
    await db.refresh(tool)
    return tool
