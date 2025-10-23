class CreateCandidates < ActiveRecord::Migration[8.0]
  def change
    create_table :candidates do |t|
      t.references :company, null: false, foreign_key: true
      t.string :name
      t.string :email
      t.jsonb :resume_data
      t.string :linkedin_url
      t.string :github_url
      t.string :external_id
      t.string :ats_provider

      t.timestamps
    end
    add_index :candidates, :email
  end
end
