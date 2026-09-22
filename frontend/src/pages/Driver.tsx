import { useEffect, useRef, useState } from "react";
import { MapPin, Radio, Truck } from "lucide-react";
import { api } from "../api";
import { useAction, useData } from "../components/ui";
import type { Availability } from "../types";
export function DriverControls() {
  const availability = useData<Availability>("/driver/availability", 15000);
  const action = useAction(() => void availability.reload());
  const [sharing, setSharing] = useState(false),
    [locationError, setLocationError] = useState(""),
    [sent, setSent] = useState(false);
  const lastSent = useRef(0);
  useEffect(() => {
    const beat = () => {
      if (document.visibilityState === "visible")
        void api("/driver/heartbeat", "POST").catch(() => {});
    };
    beat();
    const timer = setInterval(beat, 60000);
    return () => clearInterval(timer);
  }, []);
  useEffect(() => {
    if (!sharing) return;
    if (!navigator.geolocation) {
      setLocationError("المتصفح لا يدعم مشاركة الموقع.");
      setSharing(false);
      return;
    }
    const watch = navigator.geolocation.watchPosition(
      (position) => {
        if (Date.now() - lastSent.current < 15000) return;
        lastSent.current = Date.now();
        void api("/driver/location", "PUT", {
          latitude: position.coords.latitude.toFixed(7),
          longitude: position.coords.longitude.toFixed(7),
        })
          .then(() => {
            setSent(true);
            setLocationError("");
          })
          .catch((e) => setLocationError(e.message));
      },
      () => {
        setLocationError(
          "تعذّر تحديد موقعك. اسمح بالوصول للموقع من إعدادات المتصفح.",
        );
        setSharing(false);
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 },
    );
    return () => navigator.geolocation.clearWatch(watch);
  }, [sharing]);
  return (
    <>
      <section className="driver-control">
        <div className="item-avatar">
          <Truck />
        </div>
        <div className="grow">
          <strong>
            <i
              className={
                "status-dot " + (availability.data?.is_available ? "on" : "")
              }
            />
            {availability.data?.is_available
              ? "متاح لاستقبال التوصيلات"
              : "غير متاح حاليًا"}
            {availability.data?.busy ? " · عندك توصيلة نشطة" : ""}
          </strong>
          <p>
            التوفر بيتوقف بعد 30 دقيقة بدون تحديث. مشاركة الموقع للمدير فقط
            أثناء فتح الصفحة.
          </p>
        </div>
        <button
          disabled={action.busy || !availability.data}
          onClick={() =>
            void action.run(() =>
              api("/driver/availability", "PUT", {
                is_available: !availability.data?.is_available,
              }),
            )
          }
        >
          <Radio size={17} />
          {availability.data?.is_available ? "إيقاف التوفر" : "تفعيل التوفر"}
        </button>
        <button
          className={sharing ? "primary" : ""}
          onClick={() => {
            setSharing(!sharing);
            setLocationError("");
            lastSent.current = 0;
          }}
        >
          <MapPin size={17} />
          {sharing ? "إيقاف مشاركة الموقع" : "مشاركة الموقع مع المدير"}
        </button>
        {sharing && sent && (
          <small role="status">موقعك بيتحدث للمدير فقط.</small>
        )}
      </section>
      {(action.error || availability.error || locationError) && (
        <div className="error" role="alert">
          {action.error || availability.error || locationError}
        </div>
      )}
    </>
  );
}
