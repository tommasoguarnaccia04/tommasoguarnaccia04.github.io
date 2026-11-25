-- Permit safe destinations and resolve uploads relative to the current article.
local prefix = os.getenv("PORTFOLIO_PREFIX") or ""
local function normalize(target)
  if target:match("^/assets/") then
    return prefix .. target:sub(2)
  end
  if target:match("^https://") or target:match("^mailto:") or target:match("^#") then
    return target
  end
end

function Link(link)
  local target = normalize(link.target)
  if not target then
    return link.content
  end
  link.target = target
  return link
end

function Image(image)
  local target = normalize(image.src)
  if not target or target:match("^mailto:") or target:match("^#") then
    return image.caption
  end
  image.src = target
  return image
end
