export interface ConnectionTestRequest {
  connection_string: string;
}

export interface ConnectionTestResponse {
  status: string;
  message: string;
}

export interface ColumnMetadata {
  name: string;
  type: string;
  nullable: boolean;
  default?: string | null;
  native_type?: string;
  enum_values?: string[];
}

export interface ForeignKeyMetadata {
  column?: string[] | string;
  constrained_columns?: string[];
  referred_table: string;
  referred_columns: string[];
}

export interface TableSchema {
  table_name?: string;
  columns: ColumnMetadata[];
  primary_keys?: string[];
  primary_key?: string[];
  foreign_keys: ForeignKeyMetadata[];
  description?: string;
}

export interface DatabaseSchemaResponse {
  status: string;
  tables_count: number;
  schema: Record<string, TableSchema>;
}
