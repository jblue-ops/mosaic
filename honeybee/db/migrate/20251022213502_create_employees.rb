class CreateEmployees < ActiveRecord::Migration[8.0]
  def change
    create_table :employees do |t|
      t.references :company, null: false, foreign_key: true
      t.string :name
      t.string :email
      t.jsonb :internal_profile

      t.timestamps
    end
    add_index :employees, :email
  end
end
