from pydantic import BaseModel
from typing import List, Optional


class Coding(BaseModel):
    system: str
    code: str
    display: Optional[str] = None


class Category(BaseModel):
    coding: List[Coding]
    text: str


class Code(BaseModel):
    coding: List[Coding]
    text: Optional[str] = None


class ValueQuantity(BaseModel):
    value: Optional[float]
    unit: str
    system: str
    code: str


class ValueCodeableConcept(BaseModel):
    coding: List[Coding]
    text: str


class Component(BaseModel):
    code: Optional[Code]
    valueQuantity: Optional[ValueQuantity] = None
    valueCodeableConcept: Optional[ValueCodeableConcept] = None


class Reference(BaseModel):
    reference: str
    display: Optional[str] = None


class Resource(BaseModel):
    resourceType: str
    id: Optional[str] = None
    status: Optional[str] = None
    category: Optional[List[Category]] = None
    code: Optional[Code] = None
    subject: Optional[Reference] = None
    encounter: Optional[Reference] = None
    effectiveDateTime: Optional[str] = None
    issued: Optional[str] = None
    performer: Optional[List[Reference]] = None
    component: Optional[List[Component]] = None
    valueString: Optional[str] = None


class Link(BaseModel):
    relation: str
    url: str


class Entry(BaseModel):
    link: Optional[List[Link]] = None
    fullUrl: Optional[str] = None
    resource: Resource
    search: Optional[dict] = None


class InputModel(BaseModel):
    resourceType: str
    type: str
    total: int
    link: List[Link]
    entry: List[Entry]
