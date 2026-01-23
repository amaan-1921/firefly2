import { toast } from "sonner"

export const useToast = () => {
  const toastFn = ({ title, description, variant }: { title: string; description?: string; variant?: string }) => {
    const message = description ? `${title}: ${description}` : title;
    if (variant === "destructive") {
      toast.error(message);
    } else {
      toast(message);
    }
  };
  return { toast: toastFn };
}