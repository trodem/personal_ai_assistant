from contextvars import ContextVar


request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="-")
trace_id_ctx_var: ContextVar[str] = ContextVar("trace_id", default="-")
user_id_ctx_var: ContextVar[str] = ContextVar("user_id", default="-")
tenant_id_ctx_var: ContextVar[str] = ContextVar("tenant_id", default="-")
