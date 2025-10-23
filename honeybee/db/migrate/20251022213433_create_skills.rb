class CreateSkills < ActiveRecord::Migration[8.0]
  def change
    create_table :skills do |t|
      t.string :name
      t.string :category
      t.jsonb :metadata

      t.timestamps
    end
    add_index :skills, :name
  end
end
