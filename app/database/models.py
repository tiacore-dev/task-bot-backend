import uuid
import bcrypt
from tortoise import fields
from tortoise.models import Model

# Роли пользователей


class UserRole(Model):
    class Meta:
        table = "user_roles"

    role_id = fields.CharField(pk=True, max_length=50)
    role_name = fields.CharField(max_length=50, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Пользователи


async def set_password(password: str):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return password_hash


class AdminUser(Model):
    class Meta:
        table = "admin_users"

    admin_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    username = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())


class User(Model):
    class Meta:
        table = "users"

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
    class Meta:
        table = "user_accounts"

    account_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="accounts")
    platform = fields.ForeignKeyField(
        "models.TaskPlatform", related_name="user_accounts")  # ✅ ForeignKey
    account_name = fields.CharField(max_length=255)
    account_platform_id = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Платформы для заданий


class TaskPlatform(Model):
    class Meta:
        table = "task_platforms"

    platform_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    platform_name = fields.CharField(max_length=100, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Типы заданий


class TaskType(Model):
    class Meta:
        table = "task_types"

    task_type_id = fields.CharField(pk=True, max_length=50)
    task_type_name = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Типы требований к заданиям


class TaskRequirementType(Model):
    class Meta:
        table = "task_requirement_types"

    req_type_id = fields.CharField(pk=True, max_length=50)
    req_name = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Статусы заданий


class TaskStatus(Model):
    class Meta:
        table = "task_statuses"

    status_id = fields.CharField(pk=True, max_length=50)
    status_name = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

# Задания


class Task(Model):
    class Meta:
        table = "tasks"

    task_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    task_name = fields.CharField(max_length=255)
    creator = fields.ForeignKeyField(
        "models.AdminUser", related_name="tasks_created")
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
    class Meta:
        table = "task_assignments"

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
    class Meta:
        table = "task_verifications"

    verification_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    task_assignment = fields.ForeignKeyField(
        "models.TaskAssignment", related_name="verifications")
    check_date = fields.DatetimeField(null=True)
    status = fields.CharField(max_length=50, choices=[
                              "pending", "approved", "rejected"], default="pending")
    details = fields.TextField(null=True)
    s3_name = fields.CharField(max_length=255)

# Начисления пользователям


class Transaction(Model):
    class Meta:
        table = "transactions"

    transaction_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="transactions")
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = fields.CharField(
        max_length=50, choices=["credit", "debit", "withdraw"])
    task = fields.ForeignKeyField(
        "models.Task", related_name="transactions", null=True)
    created_at = fields.DatetimeField(auto_now_add=True)


class UserActionLog(Model):
    log_id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="logs")
    # Например: "создал задание", "изменил статус"
    action = fields.CharField(max_length=255)
    timestamp = fields.DatetimeField(auto_now_add=True)
    task = fields.ForeignKeyField(
        "models.Task", related_name="logs", null=True)  # Если связано с заданием

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
