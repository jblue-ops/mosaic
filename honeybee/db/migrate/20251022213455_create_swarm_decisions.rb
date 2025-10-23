class CreateSwarmDecisions < ActiveRecord::Migration[8.0]
  def change
    create_table :swarm_decisions do |t|
      t.references :candidate, null: false, foreign_key: true
      t.references :job_opening, null: false, foreign_key: true
      t.string :decision_type
      t.jsonb :agent_votes
      t.jsonb :consensus_details
      t.decimal :overall_confidence
      t.jsonb :bias_flags
      t.datetime :evaluated_at

      t.timestamps
    end
  end
end
