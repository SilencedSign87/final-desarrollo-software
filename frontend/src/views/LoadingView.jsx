import Spinner from "../components/spinner";

export default function LoadingView() {
    return (
        <div className="w-dvw h-dvh flex justify-center items-center">
            <div className="aspect-square p-8 bg-white rounded-lg shadow-lg flex justify-center items-center">
                <Spinner />
            </div>
        </div>
    )
}