class TasksController < ApplicationController
  before_action :authenticate_user!, except: %i[index show solve]
  before_action :set_task, only: %i[show edit update destroy solve]
  before_action :authorize_owner!, only: %i[edit update destroy]

  def index
    @tasks = Task.includes(:user).order(created_at: :desc)
  end

  def show
    @comments = @task.comments.includes(:user).order(created_at: :asc)
    @labyrinth_solved ||= false
    set_reward_visibility
  end

  def new
    @task = current_user.tasks.build
  end

  def create
    @task = current_user.tasks.build(task_params)
    @task.ensure_labyrinth_generated if @task.labyrinth_task_type?
    if @task.save
      redirect_to @task, notice: "Задание создано."
    else
      flash.now[:alert] = "Не удалось создать задание."
      render :new, status: :unprocessable_entity
    end
  end

  def edit; end

  def update
    @task.assign_attributes(task_params)
    @task.ensure_labyrinth_generated if @task.labyrinth_task_type?

    if @task.update(task_params)
      redirect_to @task, notice: "Задание обновлено."
    else
      flash.now[:alert] = "Не удалось обновить задание."
      render :edit, status: :unprocessable_entity
    end
  end

  def destroy
    @task.destroy
    redirect_to tasks_path, notice: "Задание удалено."
  end

  def solve
    unless @task.labyrinth_task_type?
      return redirect_to @task, alert: "Это задание не является лабиринтом."
    end

    moves = params[:moves].to_s
    @labyrinth_result = @task.simulate_labyrinth_moves(moves)
    @labyrinth_solved = @labyrinth_result[:success]
    @comments = @task.comments.includes(:user).order(created_at: :asc)
    flash.now[@labyrinth_solved ? :toast_success : :toast_error] =
      (@labyrinth_solved ? "Маршрут верный! Награда открыта." : "Маршрут неверный или упёрся в стену.")
    set_reward_visibility
    respond_to do |format|
      format.html { render :show, status: :ok }
      format.turbo_stream
    end
  end

  private

  def set_task
    @task = Task.find(params[:id])
  end

  def authorize_owner!
    return if @task.user == current_user

    redirect_to @task, alert: "Только автор может выполнять это действие."
    false
  end

  def task_params
    params.require(:task).permit(:title, :description, :reward, :reward_visibility, :task_type)
  end

  def set_reward_visibility
    @can_view_reward =
      if @task.labyrinth_task_type?
        (@labyrinth_solved || false) || (user_signed_in? && current_user == @task.user) || @task.public_reward?
      else
        @task.public_reward? || (user_signed_in? && current_user == @task.user)
      end
  end
end
