const envName = import.meta.env.VITE_ENV_NAME;

/**
 * Marks which named environment this tab is showing. Several environments
 * run the same UI on different ports, so without this they're impossible to
 * tell apart. Renders nothing for plain local dev.
 */
export function EnvBadge() {
  if (!envName || envName === "dev") {
    return null;
  }
  return (
    <div className="env-badge" aria-label={`Environment: ${envName}`}>
      {envName}
    </div>
  );
}
