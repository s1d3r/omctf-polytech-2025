class ChangeTasksUserNullability < ActiveRecord::Migration[7.2]
  def change
    change_column_null :tasks, :user_id, true
  end
end
