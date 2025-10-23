class AddCompanyToUsers < ActiveRecord::Migration[8.0]
  def change
    add_reference :users, :company, null: false, foreign_key: true
    add_column :users, :role, :integer
  end
end
