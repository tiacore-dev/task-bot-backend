import uuid
from tortoise import fields
from tortoise.models import Model

# Роли пользователей


class UserRole(Model):
    # Например: "admin", "executor"
    role_id = fields.CharField(pk=True, max_length=50)
    name = fields.CharField(max_length=50, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Пользователи


class User(Model):
    user_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    telegram_id = fields.BigIntField(unique=True)
    username = fields.CharField(max_length=255, null=True)
    role = fields.ForeignKeyField("models.UserRole", related_name="users")
    balance = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    referrer = fields.ForeignKeyField(
        "models.User", related_name="referrals", null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Аккаунты пользователей на платформах


class UserAccount(Model):
    account_id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="accounts")
    # YouTube, Twitter, Telegram и т. д.
    platform = fields.CharField(max_length=100)
    account_name = fields.CharField(max_length=255)
    # ID из соцсети, если доступно API
    account_id = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Платформы для заданий


class TaskPlatform(Model):
    platform_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=100, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Типы заданий


class TaskType(Model):
    # Например: "comment", "subscription"
    task_type_id = fields.CharField(pk=True, max_length=50)
    name = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Типы требований к заданиям


class TaskRequirementType(Model):
    # Например: "screenshot", "link"
    req_type_id = fields.CharField(pk=True, max_length=50)
    name = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Статусы заданий


class TaskStatus(Model):
    # Например: "active", "completed"
    status_id = fields.CharField(pk=True, max_length=50)
    name = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Задания


class Task(Model):
    task_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    creator = fields.ForeignKeyField(
        "models.User", related_name="tasks_created")
    platform = fields.ForeignKeyField(
        "models.TaskPlatform", related_name="tasks")
    task_type = fields.ForeignKeyField("models.TaskType", related_name="tasks")
    description = fields.TextField()
    reward = fields.DecimalField(max_digits=10, decimal_places=2)
    verification_type = fields.CharField(
        max_length=50, choices=["auto", "manual", "screenshot"])
    created_at = fields.DatetimeField(auto_now_add=True)
    status = fields.ForeignKeyField("models.TaskStatus", related_name="tasks")

# Полученные задания (исполнитель взял задание)


class TaskAssignment(Model):
    assignment_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="tasks")
    task = fields.ForeignKeyField("models.Task", related_name="assignments")
    assigned_profile = fields.ForeignKeyField(
        "models.UserAccount", related_name="assigned_tasks")
    submitted_at = fields.DatetimeField(null=True)
    status = fields.CharField(max_length=50, choices=[
                              "in_progress", "pending_review", "completed", "rejected"], default="in_progress")

# Проверки заданий


class TaskVerification(Model):
    verification_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    task_assignment = fields.ForeignKeyField(
        "models.TaskAssignment", related_name="verifications")
    check_date = fields.DatetimeField(auto_now_add=True)
    status = fields.CharField(max_length=50, choices=[
                              "pending", "approved", "rejected"], default="pending")
    details = fields.TextField(null=True)

# Начисления пользователям


class Transaction(Model):
    transaction_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="transactions")
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = fields.CharField(
        max_length=50, choices=["credit", "debit", "withdraw"])
    task = fields.ForeignKeyField(
        "models.Task", related_name="transactions", null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Лог действий пользователей


class UserActivityLog(Model):
    log_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="activity_logs")
    action = fields.CharField(max_length=255)
    timestamp = fields.DatetimeField(auto_now_add=True)
