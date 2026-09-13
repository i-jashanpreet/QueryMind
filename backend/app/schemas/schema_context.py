from pydantic import BaseModel, Field

class SchemaRelationship(BaseModel):
    from_table: str
    from_column: str
    to_table: str
    to_column: str


class SchemaColumn(BaseModel):
    name: str
    data_type: str
    nullable: bool = True
    is_primary_key: bool = False
    is_foreign_key: bool = False


class SchemaTable(BaseModel):
    name: str
    columns: list[SchemaColumn] = Field(default_factory=list)
    relationships: list[SchemaRelationship] = Field(default_factory=list)


class RelevantSchemaContext(BaseModel):
    tables: list[SchemaTable] = Field(default_factory=list)

    def to_llm_string(self) -> str:
        """
        Convert the schema objects into a clean string format suitable for the LLM prompt.
        """
        lines = []
        for table in sorted(self.tables, key=lambda t: t.name):
            lines.append(f"Table: {table.name}")
            for col in table.columns:
                parts = [f"  - {col.name} ({col.data_type})"]
                if col.is_primary_key:
                    parts.append("[PK]")
                if not col.nullable:
                    parts.append("[NOT NULL]")
                lines.append(" ".join(parts))
            
            # Print relationships as FKs
            for rel in sorted(table.relationships, key=lambda r: r.from_column):
                lines.append(f"  FK: {rel.from_column} -> {rel.to_table}({rel.to_column})")
            
            lines.append("")
            
        return "\n".join(lines).strip()
