class Comment < ApplicationRecord
  belongs_to :user
  belongs_to :task

  validates :body, presence: true, length: { minimum: 1, maximum: 2000 }
end
