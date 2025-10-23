# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.0].define(version: 2025_10_22_213539) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "candidates", force: :cascade do |t|
    t.bigint "company_id", null: false
    t.string "name"
    t.string "email"
    t.jsonb "resume_data"
    t.string "linkedin_url"
    t.string "github_url"
    t.string "external_id"
    t.string "ats_provider"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["company_id"], name: "index_candidates_on_company_id"
    t.index ["email"], name: "index_candidates_on_email"
  end

  create_table "capability_assessments", force: :cascade do |t|
    t.string "person_type", null: false
    t.bigint "person_id", null: false
    t.bigint "skill_id", null: false
    t.integer "proficiency"
    t.string "verified_by"
    t.jsonb "evidence"
    t.decimal "confidence_score"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["person_type", "person_id"], name: "index_capability_assessments_on_person"
    t.index ["skill_id"], name: "index_capability_assessments_on_skill_id"
  end

  create_table "companies", force: :cascade do |t|
    t.string "name"
    t.string "ats_provider"
    t.jsonb "ats_credentials"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "employees", force: :cascade do |t|
    t.bigint "company_id", null: false
    t.string "name"
    t.string "email"
    t.jsonb "internal_profile"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["company_id"], name: "index_employees_on_company_id"
    t.index ["email"], name: "index_employees_on_email"
  end

  create_table "job_openings", force: :cascade do |t|
    t.bigint "company_id", null: false
    t.string "title"
    t.text "description"
    t.jsonb "required_skills"
    t.integer "status"
    t.string "external_id"
    t.string "ats_provider"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["company_id"], name: "index_job_openings_on_company_id"
  end

  create_table "sessions", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "ip_address"
    t.string "user_agent"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_sessions_on_user_id"
  end

  create_table "skills", force: :cascade do |t|
    t.string "name"
    t.string "category"
    t.jsonb "metadata"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["name"], name: "index_skills_on_name"
  end

  create_table "swarm_decisions", force: :cascade do |t|
    t.bigint "candidate_id", null: false
    t.bigint "job_opening_id", null: false
    t.string "decision_type"
    t.jsonb "agent_votes"
    t.jsonb "consensus_details"
    t.decimal "overall_confidence"
    t.jsonb "bias_flags"
    t.datetime "evaluated_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["candidate_id"], name: "index_swarm_decisions_on_candidate_id"
    t.index ["job_opening_id"], name: "index_swarm_decisions_on_job_opening_id"
  end

  create_table "users", force: :cascade do |t|
    t.string "email_address", null: false
    t.string "password_digest", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "company_id", null: false
    t.integer "role"
    t.index ["company_id"], name: "index_users_on_company_id"
    t.index ["email_address"], name: "index_users_on_email_address", unique: true
  end

  add_foreign_key "candidates", "companies"
  add_foreign_key "capability_assessments", "skills"
  add_foreign_key "employees", "companies"
  add_foreign_key "job_openings", "companies"
  add_foreign_key "sessions", "users"
  add_foreign_key "swarm_decisions", "candidates"
  add_foreign_key "swarm_decisions", "job_openings"
  add_foreign_key "users", "companies"
end
