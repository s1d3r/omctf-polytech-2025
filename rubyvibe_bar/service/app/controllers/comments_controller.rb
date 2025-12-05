class CommentsController < ApplicationController
  before_action :authenticate_user!
  before_action :set_task
  before_action :set_comment, only: :destroy
  before_action :authorize_comment_action!, only: :destroy

  def create
    @comment = @task.comments.build(comment_params.merge(user: current_user))

    if @comment.save
      redirect_to task_path(@task), notice: "Сообщение оставлено в таверне."
    else
      redirect_to task_path(@task), alert: @comment.errors.full_messages.to_sentence
    end
  end

  def destroy
    @comment.destroy
    redirect_to task_path(@task), notice: "Комментарий удалён."
  end

  private

  def set_task
    @task = Task.find(params[:task_id])
  end

  def set_comment
    @comment = @task.comments.find(params[:id])
  end

  def authorize_comment_action!
    return if @comment.user == current_user || @task.user == current_user

    redirect_to task_path(@task), alert: "Удаление доступно только автору."
    false
  end

  def comment_params
    params.require(:comment).permit(:body)
  end
end
