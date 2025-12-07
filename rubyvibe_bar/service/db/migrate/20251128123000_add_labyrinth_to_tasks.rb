class AddLabyrinthToTasks < ActiveRecord::Migration[7.2]
  def change
    add_column :tasks, :task_type, :string, null: false, default: "standard"
    add_column :tasks, :labyrinth_data, :text
    add_index :tasks, :task_type
  end
end
