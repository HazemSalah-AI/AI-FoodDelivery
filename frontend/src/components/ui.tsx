import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
  type FormEvent,
} from "react";
import {
  ArrowLeft,
  LoaderCircle,
  PackageOpen,
  RefreshCw,
  X,
} from "lucide-react";
import { api, statusName } from "../api";
export function useData<T>(path: string | null, interval = 0) {
  const [data, setData] = useState<T | null>(null),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(true);
  const version = useRef(0);
  const reload = useCallback(async () => {
    if (!path) {
      setData(null);
      setLoading(false);
      return;
    }
    const request = ++version.current;
    try {
      const value = await api<T>(path);
      if (request === version.current) {
        setData(value);
        setError("");
      }
    } catch (e) {
      if (request === version.current) setError((e as Error).message);
    } finally {
      if (request === version.current) setLoading(false);
    }
  }, [path]);
  useEffect(() => {
    setData(null);
    setLoading(true);
    void reload();
    const timer = interval
      ? window.setInterval(() => void reload(), interval)
      : undefined;
    return () => {
      version.current++;
      if (timer) clearInterval(timer);
    };
  }, [reload, interval]);
  return { data, error, loading, reload };
}
export function State({
  loading,
  error,
  empty,
  retry,
  children,
}: {
  loading?: boolean;
  error?: string;
  empty?: boolean;
  retry?: () => void;
  children: ReactNode;
}) {
  if (loading)
    return (
      <div className="empty" role="status">
        <LoaderCircle className="spin" /> بنحمّل البيانات…
      </div>
    );
  if (error)
    return (
      <div className="error" role="alert">
        {error}
        {retry && (
          <button onClick={retry}>
            <RefreshCw size={16} />
            حاول مرة أخرى
          </button>
        )}
      </div>
    );
  if (empty)
    return (
      <div className="empty">
        <PackageOpen size={40} />
        <h3>لسه مفيش بيانات هنا</h3>
        <p>هتظهر هنا بمجرد إضافتها.</p>
      </div>
    );
  return <>{children}</>;
}
export function Badge({ status }: { status: string }) {
  return (
    <span className={"badge status-" + status}>
      {statusName[status] ?? status}
    </span>
  );
}
export function Header({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  );
}
export function Modal({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    ref.current?.showModal();
    const previous = document.activeElement as HTMLElement;
    return () => {
      ref.current?.close();
      previous?.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === ref.current) onClose();
      }}
    >
      <div className="modal-head">
        <h2>{title}</h2>
        <button className="icon" aria-label="إغلاق" onClick={onClose}>
          <X />
        </button>
      </div>
      {children}
    </dialog>
  );
}
export function Form({
  children,
  onSubmit,
  submit = "حفظ",
  className = "",
}: {
  children: ReactNode;
  onSubmit: (data: FormData) => Promise<void>;
  submit?: string;
  className?: string;
}) {
  const [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  async function send(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await onSubmit(new FormData(e.currentTarget));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className={"form " + className} onSubmit={send}>
      {children}
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      <button className="primary" disabled={busy} type="submit">
        {busy ? <LoaderCircle className="spin" size={18} /> : null}
        {busy ? "جارٍ الحفظ…" : submit}
        <ArrowLeft size={17} />
      </button>
    </form>
  );
}
export function Field({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
    </label>
  );
}
export function Pages({
  page,
  total,
  onChange,
  size = 12,
}: {
  page: number;
  total: number;
  onChange: (page: number) => void;
  size?: number;
}) {
  return total > size ? (
    <div className="pagination">
      <button disabled={page === 1} onClick={() => onChange(page - 1)}>
        السابق
      </button>
      <span>
        صفحة {page} من {Math.ceil(total / size)}
      </span>
      <button
        disabled={page * size >= total}
        onClick={() => onChange(page + 1)}
      >
        التالي
      </button>
    </div>
  ) : null;
}
export function useAction(reload?: () => void) {
  const [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  async function run(action: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    try {
      await action();
      reload?.();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return { busy, error, run };
}
export const val = (data: FormData, key: string) => String(data.get(key) ?? "");
