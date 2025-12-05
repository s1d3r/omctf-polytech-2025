class CreateTasks < ActiveRecord::Migration[7.2]
  def change
    create_table :tasks do |t|
      t.string :title, null: false, limit: 150
      t.text :description, null: false
      t.string :reward, null: false, limit: 255
      t.integer :reward_visibility, null: false, default: 0
      t.references :user, null: false, foreign_key: true

      t.timestamps
    end
  end
end
