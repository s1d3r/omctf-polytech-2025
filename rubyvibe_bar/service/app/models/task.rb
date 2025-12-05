class Task < ApplicationRecord
  belongs_to :user
  has_many :comments, dependent: :destroy

  enum :reward_visibility, { public_reward: 0, private_reward: 1 }
  enum :task_type, { standard: "standard", labyrinth: "labyrinth" }, suffix: true

  before_validation :set_default_task_type
  before_validation :ensure_labyrinth_generated, if: :labyrinth_task_type?

  validates :title, presence: true, length: { minimum: 5, maximum: 150 }
  validates :description, presence: true
  validates :reward, presence: true, length: { maximum: 255 }
  validates :reward_visibility, presence: true, inclusion: { in: reward_visibilities.keys }
  validates :task_type, inclusion: { in: task_types.keys }
  validate :validate_labyrinth_payload

  def labyrinth_payload
    return unless labyrinth_data.present?

    @labyrinth_payload ||= JSON.parse(labyrinth_data).with_indifferent_access
  rescue JSON::ParserError
    nil
  end

  def labyrinth_solution
    labyrinth_payload&.dig(:solution)
  end

  def labyrinth_grid
    labyrinth_payload&.dig(:grid)&.map(&:chars)
  end

  def start_cell
    arr = labyrinth_payload&.dig(:start)
    arr&.map(&:to_i)
  end

  def finish_cell
    arr = labyrinth_payload&.dig(:finish)
    arr&.map(&:to_i)
  end

  def simulate_labyrinth_moves(moves)
    return { success: false, reason: :no_labyrinth } unless labyrinth_task_type? && labyrinth_payload && labyrinth_grid

    sanitized = moves.to_s.upcase.gsub(/[^UDLR]/, "")
    grid = labyrinth_grid
    h = grid.length
    w = grid.first.length
    pos = start_cell
    return { success: false, reason: :invalid_start } unless pos && finish_cell

    path_valid = true
    sanitized.chars.each do |ch|
      np = next_pos(pos, ch)
      if np[0].negative? || np[1].negative? || np[0] >= h || np[1] >= w || grid[np[0]][np[1]] == "1"
        path_valid = false
        break
      end
      pos = np
    end

    success = path_valid && pos == finish_cell && sanitized == labyrinth_solution.to_s
    { success: success, path_valid: path_valid, ended_at_finish: pos == finish_cell, moves: sanitized }
  end

  def ensure_labyrinth_generated
    return if labyrinth_payload.present?

    self.labyrinth_data = generate_labyrinth.to_json
  end

  private

  def set_default_task_type
    self.task_type ||= "standard"
  end

  def validate_labyrinth_payload
    return unless labyrinth_task_type?

    if labyrinth_payload.blank?
      errors.add(:labyrinth_data, "должна быть сгенерирована для лабиринта")
      return
    end

    %i[width height grid start finish solution].each do |key|
      errors.add(:labyrinth_data, "отсутствует поле #{key}") unless labyrinth_payload.key?(key)
    end
  end

  def generate_labyrinth(width: 29, height: 21)
    width += 1 if width.even?
    height += 1 if height.even?

    grid = Array.new(height) { Array.new(width, 1) }
    start = [0, 0]
    finish = [height - 1, width - 1]

    grid[start[0]][start[1]] = 0
    frontier = neighbors_two_steps(start, width, height)

    while frontier.any?
      cell = frontier.delete(frontier.sample)
      next unless cell

      carved_neighbors = neighbors_two_steps(cell, width, height).select { |(r, c)| grid[r][c] == 0 }
      next if carved_neighbors.empty?

      neighbor = carved_neighbors.sample
      between = [(cell[0] + neighbor[0]) / 2, (cell[1] + neighbor[1]) / 2]

      grid[cell[0]][cell[1]] = 0
      grid[between[0]][between[1]] = 0

      frontier.concat(neighbors_two_steps(cell, width, height).select { |(r, c)| grid[r][c] == 1 })
      frontier.uniq!
    end

    grid[finish[0]][finish[1]] = 0
    solution = shortest_path(grid, start, finish)

    {
      width: width,
      height: height,
      grid: grid.map { |row| row.join },
      start: start,
      finish: finish,
      solution: solution
    }
  end

  def neighbors_two_steps(cell, width, height)
    r, c = cell
    [[r - 2, c], [r + 2, c], [r, c - 2], [r, c + 2]].select do |nr, nc|
      nr.between?(0, height - 1) && nc.between?(0, width - 1)
    end
  end

  def neighbors_one(cell, width, height)
    r, c = cell
    [[r - 1, c, "U"], [r + 1, c, "D"], [r, c - 1, "L"], [r, c + 1, "R"]].select do |nr, nc, _|
      nr.between?(0, height - 1) && nc.between?(0, width - 1)
    end
  end

  def shortest_path(grid, start, finish)
    h = grid.length
    w = grid.first.length
    queue = [start]
    visited = { start => nil }
    dirs = {}

    until queue.empty?
      cell = queue.shift
      break if cell == finish

      neighbors_one(cell, w, h).each do |nr, nc, dir|
        next if grid[nr][nc] == 1
        next if visited.key?([nr, nc])

        visited[[nr, nc]] = cell
        dirs[[nr, nc]] = dir
        queue << [nr, nc]
      end
    end

    return "" unless visited.key?(finish)

    path_dirs = []
    cur = finish
    while cur != start
      dir = dirs[cur]
      path_dirs << dir
      cur = visited[cur]
    end

    path_dirs.reverse.join
  end

  def next_pos(pos, dir)
    r, c = pos
    case dir
    when "U" then [r - 1, c]
    when "D" then [r + 1, c]
    when "L" then [r, c - 1]
    when "R" then [r, c + 1]
    else pos
    end
  end
end
