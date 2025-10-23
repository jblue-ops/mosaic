class CreateJobOpenings < ActiveRecord::Migration[8.0]
  def change
    create_table :job_openings do |t|
      t.references :company, null: false, foreign_key: true
      t.string :title
      t.text :description
      t.jsonb :required_skills
      t.integer :status
      t.string :external_id
      t.string :ats_provider

      t.timestamps
    end
  end
end
