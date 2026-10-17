import type { User } from "../api";

export default function Avatar({ user, size = 40 }: { user: User; size?: number }) {
  const style = { width: size, height: size, fontSize: size * 0.42 };
  if (user.avatar_url) {
    return <img className="avatar" src={user.avatar_url} alt="" style={style} />;
  }
  return (
    <span className="avatar avatar-initial" style={style} aria-hidden="true">
      {user.username.charAt(0).toUpperCase()}
    </span>
  );
}
