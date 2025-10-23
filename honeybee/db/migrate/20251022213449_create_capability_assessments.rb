class CreateCapabilityAssessments < ActiveRecord::Migration[8.0]
  def change
    create_table :capability_assessments do |t|
      t.references :person, polymorphic: true, null: false
      t.references :skill, null: false, foreign_key: true
      t.integer :proficiency
      t.string :verified_by
      t.jsonb :evidence
      t.decimal :confidence_score

      t.timestamps
    end
  end
end
